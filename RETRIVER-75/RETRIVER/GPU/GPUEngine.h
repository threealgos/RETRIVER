/*
* This file is part of the BTCCollider distribution (https://github.com/JeanLucPons/Kangaroo).
* Copyright (c) 2020 Jean Luc PONS.
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, version 3.
*
* This program is distributed in the hope that it will be useful, but
* WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
* General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program. If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef GPUENGINEH
#define GPUENGINEH

#include <vector>
#include "../Constants.h"
#include "../SECPK1/SECP256k1.h"

#ifdef USE_SYMMETRY
#define KSIZE 11
#else
#define KSIZE 10
#endif

#define ITEM_SIZE   56
#define ITEM_SIZE32 (ITEM_SIZE/4)
// Kangaroo types
#define TAME2 2   // Wild2 kangaroo
#define TAME3 3   // Wild3 kangaroo
#define TAME4 4   // Wild4 kangaroo
#define TAME5 5   // Wild5 kangaroo
#define TAME6 6   // Wild6 kangaroo
#define TAME7 7   // Wild7 kangaroo
#define TAME8 8   // Wild8 kangaroo
#define TAME9 9   // Wild9 kangaroo
#define TAME10 10   // TAME10 kangaroo
#define TAME11 11   // TAME11 kangaroo
#define TAME12 12   // TAME12 kangaroo
#define TAME13 13   // TAME13 kangaroo
#define TAME14 14   // TAME14 kangaroo
#define TAME15 15   // TAME15 kangaroo
#define TAME16 16   // TAME16 kangaroo
#define TAME17 17   // TAME17 kangaroo
#define TAME18 18   // TAME18 kangaroo
#define TAME19 19   // TAME19 kangaroo
#define TAME20 20   // TAME20 kangaroo
#define TAME21 21   // TAME21 kangaroo
#define TAME22 22   // TAME22 kangaroo
#define TAME23 23   // TAME23 kangaroo
#define TAME24 24   // TAME24 kangaroo
#define TAME25 25   // TAME25 kangaroo
#define TAME26 26   // TAME26 kangaroo
#define TAME27 27   // TAME27 kangaroo
#define TAME28 28   // TAME28 kangaroo
#define TAME29 29   // TAME29 kangaroo
#define TAME30 30   // TAME30 kangaroo
#define TAME31 31   // TAME31 kangaroo
#define TAME32 32   // TAME32 kangaroo
#define TAME33 33   // TAME33 kangaroo
#define TAME34 34   // TAME34 kangaroo
#define TAME35 35   // TAME35 kangaroo
#define TAME36 36   // TAME36 kangaroo
#define TAME37 37   // TAME37 kangaroo
#define TAME38 38   // TAME38 kangaroo
#define TAME39 39   // TAME39 kangaroo
#define TAME40 40   // TAME40 kangaroo
#define TAME41 41   // TAME41 kangaroo
#define TAME42 42   // TAME42 kangaroo
#define TAME43 43   // TAME43 kangaroo
#define TAME44 44   // TAME44 kangaroo
#define TAME45 45   // TAME45 kangaroo
#define TAME46 46   // TAME46 kangaroo
#define TAME47 47   // TAME47 kangaroo
#define TAME48 48   // TAME48 kangaroo
#define TAME49 49   // TAME49 kangaroo
#define TAME50 50   // TAME50 kangaroo
#define WILD2 2   // Wild2 kangaroo
#define WILD3 3   // Wild3 kangaroo
#define WILD4 4   // Wild4 kangaroo
#define WILD5 5   // Wild5 kangaroo
#define WILD6 6   // Wild6 kangaroo
#define WILD7 7   // Wild7 kangaroo
#define WILD8 8   // Wild8 kangaroo
#define WILD9 9   // Wild9 kangaroo
#define WILD10 10   // Wild10 kangaroo
#define WILD11 11   // Wild11 kangaroo
#define WILD12 12   // Wild12 kangaroo
#define WILD13 13   // Wild13 kangaroo
#define WILD14 14   // Wild14 kangaroo
#define WILD15 15   // Wild15 kangaroo
#define WILD16 16   // Wild16 kangaroo
#define WILD17 17   // Wild17 kangaroo
#define WILD18 18   // Wild18 kangaroo
#define WILD19 19   // Wild19 kangaroo
#define WILD20 20   // Wild20 kangaroo
#define WILD21 21   // Wild21 kangaroo
#define WILD22 22   // Wild22 kangaroo
#define WILD23 23   // Wild23 kangaroo
#define WILD24 24   // Wild24 kangaroo
#define WILD25 25   // Wild25 kangaroo
#define WILD26 26   // Wild26 kangaroo
#define WILD27 27   // Wild27 kangaroo
#define WILD28 28   // Wild28 kangaroo
#define WILD29 29   // Wild29 kangaroo
#define WILD30 30   // Wild30 kangaroo
#define WILD31 31   // Wild31 kangaroo
#define WILD32 32   // Wild32 kangaroo
#define WILD33 33   // Wild33 kangaroo
#define WILD34 34   // Wild34 kangaroo
#define WILD35 35   // Wild35 kangaroo
#define WILD36 36   // Wild36 kangaroo
#define WILD37 37   // Wild37 kangaroo
#define WILD38 38   // Wild38 kangaroo
#define WILD39 39   // Wild39 kangaroo
#define WILD40 40   // Wild40 kangaroo
#define WILD41 41   // Wild41 kangaroo
#define WILD42 42   // Wild42 kangaroo
#define WILD43 43   // Wild43 kangaroo
#define WILD44 44   // Wild44 kangaroo
#define WILD45 45   // Wild45 kangaroo
#define WILD46 46   // Wild46 kangaroo
#define WILD47 47   // Wild47 kangaroo
#define WILD48 48   // Wild48 kangaroo
#define WILD49 49   // Wild49 kangaroo
#define WILD50 50   // Wild50 kangaroo

typedef struct {
  Int x;
  Int d;
  uint64_t kIdx;
} ITEM;

class GPUEngine {

public:

  GPUEngine(int nbThreadGroup,int nbThreadPerGroup,int gpuId,uint32_t maxFound);
  ~GPUEngine();
  void SetParams(uint64_t dpMask,Int *distance,Int *px,Int *py);
  void SetKangaroos(Int *px,Int *py,Int *d);
  void GetKangaroos(Int *px,Int *py,Int *d);
  void SetKangaroo(uint64_t kIdx,Int *px,Int *py,Int *d);
  bool Launch(std::vector<ITEM> &hashFound,bool spinWait = false);
  Int CalculateWildOffset(int wildType);
  void SetWildOffset(Int *offset);
  int GetNbThread();
  int GetGroupSize();
  int GetMemory();
  bool callKernelAndWait();
  bool callKernel();

  std::string deviceName;

  static void *AllocatePinnedMemory(size_t size);
  static void FreePinnedMemory(void *buff);
  static void PrintCudaInfo();
  static bool GetGridSize(int gpuId,int *x,int *y);

private:

  Int wildOffset;
  int nbThread;
  int nbThreadPerGroup;
  uint64_t *inputKangaroo;
  uint64_t *inputKangarooPinned;
  uint32_t *outputItem;
  uint32_t *outputItemPinned;
  uint64_t *jumpPinned;
  bool initialised;
  bool lostWarning;
  uint32_t maxFound;
  uint32_t outputSize;
  uint32_t kangarooSize;
  uint32_t kangarooSizePinned;
  uint32_t jumpSize;
  uint64_t dpMask;

};

#endif // GPUENGINEH
