using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;
using FeatureWorkflow.VerifyDocxCli.Styles;

namespace FeatureWorkflow.VerifyDocxCli.Rendering;

public static class StyleRegistrar
{
    public static void Register(MainDocumentPart mainPart, IBrandStyle style)
    {
        var stylesPart = mainPart.AddNewPart<StyleDefinitionsPart>();
        stylesPart.Styles = new DocumentFormat.OpenXml.Wordprocessing.Styles(
            BuildHeadingStyle("Heading1", "標題 1", outlineLevel: 0, sizeHalfPt: 32, style),
            BuildHeadingStyle("Heading2", "標題 2", outlineLevel: 1, sizeHalfPt: 28, style),
            BuildHeadingStyle("Heading3", "標題 3", outlineLevel: 2, sizeHalfPt: 24, style),
            BuildNormalStyle(style),
            BuildCodeStyle(style));
    }

    private static Style BuildHeadingStyle(string id, string name, int outlineLevel, int sizeHalfPt, IBrandStyle style)
        => new Style(
            new StyleName { Val = name },
            new BasedOn { Val = "Normal" },
            new NextParagraphStyle { Val = "Normal" },
            new StyleParagraphProperties(
                new SpacingBetweenLines { Before = "240", After = "120" },
                new OutlineLevel { Val = outlineLevel }),
            new StyleRunProperties(
                new RunFonts { Ascii = style.LatinFont, EastAsia = style.CjkFont },
                new Bold(),
                new Color { Val = style.TitleColor },
                new FontSize { Val = sizeHalfPt.ToString() }))
        { Type = StyleValues.Paragraph, StyleId = id };

    private static Style BuildNormalStyle(IBrandStyle style)
        => new Style(
            new StyleName { Val = "Normal" },
            new StyleRunProperties(
                new RunFonts { Ascii = style.LatinFont, EastAsia = style.CjkFont },
                new FontSize { Val = "20" })) // 10pt
        { Type = StyleValues.Paragraph, StyleId = "Normal", Default = true };

    private static Style BuildCodeStyle(IBrandStyle style)
        => new Style(
            new StyleName { Val = "Code" },
            new BasedOn { Val = "Normal" },
            new StyleParagraphProperties(
                new Shading { Val = ShadingPatternValues.Clear, Color = "auto", Fill = "F2F2F2" }),
            new StyleRunProperties(
                new RunFonts { Ascii = "Consolas", EastAsia = style.CjkFont },
                new FontSize { Val = "16" })) // 8pt
        { Type = StyleValues.Paragraph, StyleId = "Code" };
}
