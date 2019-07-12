#include "korali.h"

using namespace Korali::Conduit;

#define MPI_TAG_CONTINUE 0
#define MPI_TAG_FITNESS 1
#define MPI_TAG_SAMPLE 2

/************************************************************************/
/*                  Constructor / Destructor Methods                    */
/************************************************************************/

void Linked::initialize()
{
 _currentSample = 0;
 _continueEvaluations = true;

 _rankCount = 1;
 _rankId = 0;

 #ifdef _KORALI_USE_MPI
 int isInitialized;
 MPI_Initialized(&isInitialized);
 if (isInitialized == false)  MPI_Init(nullptr, nullptr);

 MPI_Comm_size(MPI_COMM_WORLD, &_rankCount);
 MPI_Comm_rank(MPI_COMM_WORLD, &_rankId);
 #endif

 if (_rankCount == 1) return;

 #ifdef _KORALI_USE_MPI

 _teamCount = (_rankCount-1) / _ranksPerTeam;
 _teamId = -1;
 _localRankId = -1;

 int currentRank = 0;
 for (int i = 0; i < _teamCount; i++)
 {
   _teamQueue.push(i);
   for (int j = 0; j < _ranksPerTeam; j++)
   {
     if (currentRank == _rankId)
     {
       _teamId = i;
       _localRankId = j;
     }
     _teamWorkers[i].push_back(currentRank++);
   }
 }

 _teamSampleId.resize(_teamCount);
 _teamFitness.resize(_teamCount);
 _teamRequests.resize(_teamCount);
 _teamBusy.resize(_teamCount);

 MPI_Comm_split(MPI_COMM_WORLD, _teamId, _rankId, &_teamComm);

 int mpiSize = -1;
 MPI_Comm_size(MPI_COMM_WORLD, &mpiSize);


 if(isRoot()) if (_rankCount < _ranksPerTeam + 1)
 {
  fprintf(stderr, "[Korali] Error: You are running Korali with %d ranks. \n", _rankCount);
  fprintf(stderr, "[Korali] However, you need at least %d ranks to have at least one worker team. \n", _ranksPerTeam + 1);
  exit(-1);
 }

 MPI_Barrier(MPI_COMM_WORLD);

 if (!isRoot()) workerThread();

 #endif
}


/************************************************************************/
/*                    Configuration Methods                             */
/************************************************************************/


void Linked::getConfiguration()
{
 _k->_js["Conduit"]["Type"] = "Linked";
 _k->_js["Conduit"]["Ranks Per Team"] = _ranksPerTeam;
}

void Linked::setConfiguration()
{
 _ranksPerTeam = consume(_k->_js, { "Conduit", "Ranks Per Team" }, KORALI_NUMBER, std::to_string(1));
}

/************************************************************************/
/*                    Functional Methods                                */
/************************************************************************/

void Linked::finalize()
{
 #ifdef _KORALI_USE_MPI
 if (isRoot())
  {
   int continueFlag = 0;
    for (int i = 0; i < _teamCount; i++)
      for (int j = 0; j < _ranksPerTeam; j++)
      MPI_Send(&continueFlag, 1, MPI_INT, _teamWorkers[i][j], MPI_TAG_CONTINUE, MPI_COMM_WORLD);
  }

  MPI_Barrier(MPI_COMM_WORLD);
 #endif
}

void Linked::workerThread()
{
 #ifdef _KORALI_USE_MPI
 if (_teamId == -1) return;

 int continueFlag = 1;
 while (continueFlag == 1)
 {
  MPI_Recv(&continueFlag, 1, MPI_INT, getRootRank(), MPI_TAG_CONTINUE, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
  if (continueFlag == 1)
  {
   double sample[_k->N];
   MPI_Recv(&sample, _k->N, MPI_DOUBLE, getRootRank(), MPI_TAG_SAMPLE, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
   bool isLeader = (_localRankId == 0);

   Korali::ModelData data;
   data._comm = _teamComm;
   data._hashId = _rankId * 0x100000 + _currentSample++;

   _k->_problem->packVariables(sample, data);

   _k->_model(data);

   if (isLeader)
   {
    double fitness = _k->_problem->evaluateFitness(data);
    MPI_Send(&fitness, 1, MPI_DOUBLE, getRootRank(), MPI_TAG_FITNESS, MPI_COMM_WORLD);
   }

   MPI_Barrier(_teamComm);
  }
 }
 #endif
}

void Linked::evaluateSample(double* sampleArray, size_t sampleId)
{
 _k->functionEvaluationCount++;

 // If Sequential solver, just run the evaluation
 if (_rankCount == 1)
 {
   Korali::ModelData data;

  _k->_problem->packVariables(&sampleArray[_k->N*sampleId], data);
  data._hashId = _currentSample++;
  _k->_model(data);

  double fitness = _k->_problem->evaluateFitness(data);
  _k->functionEvaluationCount++;
  _k->_solver->processSample(sampleId, fitness);
  return;
 }

 // If parallel solver, check the workers queue.
 #ifdef _KORALI_USE_MPI
 while (_teamQueue.empty()) checkProgress();

 int teamId = _teamQueue.front(); _teamQueue.pop();
 _teamSampleId[teamId] = sampleId;


 MPI_Irecv(&_teamFitness[teamId], 1, MPI_DOUBLE, _teamWorkers[teamId][0], MPI_TAG_FITNESS, MPI_COMM_WORLD, &_teamRequests[teamId]);
 _teamBusy[teamId] = true;

 for (int i = 0; i < _ranksPerTeam; i++)
 {
  int workerId = _teamWorkers[teamId][i];
  int continueFlag = 1;
  MPI_Send(&continueFlag, 1, MPI_INT, workerId, MPI_TAG_CONTINUE, MPI_COMM_WORLD);
  MPI_Send(&sampleArray[sampleId*_k->N],_k->N, MPI_DOUBLE, workerId, MPI_TAG_SAMPLE, MPI_COMM_WORLD);
 }
 #endif
}

void Linked::checkProgress()
{
 if (_rankCount == 1) return;

 #ifdef _KORALI_USE_MPI
 for (int i = 0; i < _teamCount; i++) if (_teamBusy[i] == true)
 {
  int flag;
  MPI_Test(&_teamRequests[i], &flag, MPI_STATUS_IGNORE);
  if (flag)
  {
   _k->_solver->processSample(_teamSampleId[i], _teamFitness[i]);
   _teamBusy[i] = false;
   _teamQueue.push(i);
  }
 }
 #endif
}

int Linked::getRootRank()
{
 return _rankCount-1;
}

bool Linked::isRoot()
{
 return _rankId == getRootRank();
}