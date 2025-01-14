import 'dart:async';

class EpochDelta {
  //Calculates seconds since epoch
  // Store the initial timestamp
  EpochDelta() {
    initialTimestamp = DateTime.now();
  }
  late DateTime initialTimestamp;

  void reset() {
    initialTimestamp = DateTime.now();
  }

  int secSinceEpoch() {
    Duration difference = DateTime.now().difference(initialTimestamp);
    int secondsPassed = difference.inSeconds;
    return secondsPassed;
  }
}

//Example
void main() async {
  EpochDelta epochDelta = EpochDelta();
  Timer(const Duration(seconds: 15), () => print(epochDelta.secSinceEpoch()));
}
