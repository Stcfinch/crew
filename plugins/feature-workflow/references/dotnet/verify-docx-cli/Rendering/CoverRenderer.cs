using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;
using FeatureWorkflow.VerifyDocxCli.Markdown;
using FeatureWorkflow.VerifyDocxCli.Styles;

namespace FeatureWorkflow.VerifyDocxCli.Rendering;

public sealed class CoverRenderer
{
    private const long EmuPerInch = 914400L;
    private readonly MainDocumentPart _mainPart;
    private readonly IBrandStyle _style;
    private readonly string? _logoPath;

    public CoverRenderer(MainDocumentPart mainPart, IBrandStyle style, string? logoPath)
    {
        _mainPart = mainPart;
        _style = style;
        _logoPath = logoPath;
    }

    public void Render(Body body, CoverInfo cover)
    {
        if (_style.ShowLogo && _logoPath != null && File.Exists(_logoPath))
            body.AppendChild(ImageInserter.InlineImage(_mainPart, _logoPath, (long)(2.0 * EmuPerInch)));

        body.AppendChild(BuildTitle(cover.Project, 48));
        body.AppendChild(BuildTitle($"{cover.Feature} — 驗收報告", 32));
        body.AppendChild(ParagraphBuilder.Empty());
        body.AppendChild(BuildInfoTable(cover));
        body.AppendChild(BuildDecorationLine());
        body.AppendChild(new Paragraph(new Run(new Break { Type = BreakValues.Page })));
    }

    private Paragraph BuildTitle(string text, int sizeHalfPt)
    {
        // CT_RPr sequence: rFonts, b, ..., color, ..., sz
        var rPr = new RunProperties(
            new RunFonts { Ascii = _style.LatinFont, EastAsia = _style.CjkFont },
            new Bold(),
            new Color { Val = _style.TitleColor },
            new FontSize { Val = sizeHalfPt.ToString() });
        // CT_PPr sequence: spacing before jc
        return new Paragraph(
            new ParagraphProperties(
                new SpacingBetweenLines { Before = "240", After = "120" },
                new Justification { Val = JustificationValues.Center }),
            ParagraphBuilder.TextRun(text, rPr));
    }

    private Table BuildInfoTable(CoverInfo cover)
        => TableBuilder.BuildSimple(new[]
        {
            new[] { "項目", "內容" },
            new[] { "專案", cover.Project },
            new[] { "功能", cover.Feature },
            new[] { "版本", cover.Version },
            new[] { "製作人", cover.Author },
            new[] { "日期", cover.Date },
            new[] { "承辦單位", cover.Company },
        }, _style);

    private Paragraph BuildDecorationLine()
    {
        switch (_style.CoverDecorationHint)
        {
            case "code-bar":
                var rPr = new RunProperties(
                    new RunFonts { Ascii = "Consolas" },
                    new Color { Val = _style.AccentColor });
                return new Paragraph(
                    new ParagraphProperties(new Justification { Val = JustificationValues.Center }),
                    ParagraphBuilder.TextRun(">>> verification report >>>", rPr));

            case "orange-line":
                return new Paragraph(new ParagraphProperties(
                    new ParagraphBorders(new BottomBorder
                    {
                        Val = BorderValues.Single,
                        Color = _style.AccentColor,
                        Size = 18U,
                        Space = 1U
                    })));

            default:
                return new Paragraph();
        }
    }
}
