// Clean up and upscale the Instagram reel covers with macOS Core Image (no extra installs).
//
//   swift tools/enhance_photos.swift <input-dir> <output-dir> [scale]
//
// For each .jpg: light noise reduction (JPEG blocking), Lanczos upscale (e.g. 1.25×),
// gentle unsharp mask, saved as sRGB JPEG (quality 0.82). This sharpens what is there;
// it cannot add detail that the source does not have.
import CoreImage
import Foundation

let args = CommandLine.arguments
guard args.count >= 3 else {
    print("usage: swift enhance_photos.swift <input-dir> <output-dir> [scale]")
    exit(1)
}
let inDir = URL(fileURLWithPath: args[1])
let outDir = URL(fileURLWithPath: args[2])
let scale = args.count > 3 ? Double(args[3]) ?? 1.25 : 1.25

try FileManager.default.createDirectory(at: outDir, withIntermediateDirectories: true)
let context = CIContext(options: [.workingColorSpace: CGColorSpace(name: CGColorSpace.sRGB)!])
let srgb = CGColorSpace(name: CGColorSpace.sRGB)!

let files = try FileManager.default.contentsOfDirectory(at: inDir, includingPropertiesForKeys: nil)
    .filter { $0.pathExtension.lowercased() == "jpg" }
    .sorted { $0.lastPathComponent < $1.lastPathComponent }

for file in files {
    guard let input = CIImage(contentsOf: file) else {
        print("skip (unreadable): \(file.lastPathComponent)")
        continue
    }
    var img = input.applyingFilter("CINoiseReduction", parameters: [
        "inputNoiseLevel": 0.015,
        "inputSharpness": 0.35,
    ])
    img = img.applyingFilter("CILanczosScaleTransform", parameters: [
        kCIInputScaleKey: scale,
        kCIInputAspectRatioKey: 1.0,
    ])
    img = img.applyingFilter("CIUnsharpMask", parameters: [
        kCIInputRadiusKey: 1.6 * scale,
        kCIInputIntensityKey: 0.45,
    ])
    // Filters can grow the extent by a pixel or two; keep the exact scaled frame.
    let w = (input.extent.width * scale).rounded(), h = (input.extent.height * scale).rounded()
    img = img.cropped(to: CGRect(x: 0, y: 0, width: w, height: h))

    let out = outDir.appendingPathComponent(file.lastPathComponent)
    try context.writeJPEGRepresentation(
        of: img, to: out, colorSpace: srgb,
        options: [CIImageRepresentationOption(rawValue: kCGImageDestinationLossyCompressionQuality as String): 0.82])
    print("\(file.lastPathComponent): \(Int(input.extent.width))×\(Int(input.extent.height)) → \(Int(w))×\(Int(h))")
}
