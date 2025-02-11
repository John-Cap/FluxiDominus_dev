import '../ui/draw_arrow.dart';

class ConnectionParams {
  final String destElementId;
  final ArrowParams arrowParams;
  double tubingVolume; // Stores volume or flow resistance parameter
  String tubingType; // Allows selection of tubing material/type

  ConnectionParams({
    required this.destElementId,
    required this.arrowParams,
    this.tubingVolume =
        1.0, // Default to 1.0 mL (or any other relevant default)
    this.tubingType = "Standard",
  });

  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'destElementId': destElementId,
      'arrowParams': arrowParams.toMap(),
      'tubingVolume': tubingVolume,
      'tubingType': tubingType,
    };
  }

  factory ConnectionParams.fromMap(Map<String, dynamic> map) {
    return ConnectionParams(
      destElementId: map['destElementId'] as String,
      arrowParams:
          ArrowParams.fromMap(map['arrowParams'] as Map<String, dynamic>),
      tubingVolume: map['tubingVolume']?.toDouble() ?? 1.0,
      tubingType: map['tubingType'] ?? "Standard",
    );
  }
}
