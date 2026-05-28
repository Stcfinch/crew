using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;
using MiniMaxAIDocx.Core.Samples;

namespace FeatureWorkflow.VerifyDocxCli.Rendering;

public static class ImageInserter
{
    private const long EmuPerInch = 914400L;
    private static uint _docPropId = 1000; // logo + 截圖共用，避免 id 衝突

    public static Paragraph InlineImage(MainDocumentPart mainPart, string imagePath, long widthEmu)
    {
        var imagePart = mainPart.AddImagePart(GetImagePartType(imagePath));
        using (var stream = File.OpenRead(imagePath))
            imagePart.FeedData(stream);
        var relId = mainPart.GetIdOfPart(imagePart);

        // 依原圖比例縮到 widthEmu 寬
        var (cx, cy) = ImageSamples.CalculateImageDimensions(imagePath, widthEmu / (double)EmuPerInch);
        uint id = _docPropId++;
        var drawing = ImageSamples.BuildDrawingElement(relId, cx, cy, id, $"img{id}", null);

        return new Paragraph(
            new ParagraphProperties(new Justification { Val = JustificationValues.Center }),
            new Run(drawing));
    }

    private static PartTypeInfo GetImagePartType(string path) =>
        Path.GetExtension(path).ToLowerInvariant() switch
        {
            ".png" => ImagePartType.Png,
            ".jpg" or ".jpeg" => ImagePartType.Jpeg,
            ".gif" => ImagePartType.Gif,
            ".bmp" => ImagePartType.Bmp,
            _ => ImagePartType.Png
        };
}
