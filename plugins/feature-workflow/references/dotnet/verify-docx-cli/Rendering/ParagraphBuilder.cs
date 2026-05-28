using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Wordprocessing;

namespace FeatureWorkflow.VerifyDocxCli.Rendering;

public static class ParagraphBuilder
{
    public static Paragraph Heading(string text, string styleId)
        => new Paragraph(
            new ParagraphProperties(new ParagraphStyleId { Val = styleId }),
            TextRun(text));

    public static Paragraph Body(string text)
        => new Paragraph(TextRun(text));

    public static Paragraph Code(string text)
        => new Paragraph(
            new ParagraphProperties(new ParagraphStyleId { Val = "Code" }),
            TextRun(text));

    public static Paragraph Empty() => new Paragraph();

    // OpenXML 的 <w:t> 不保留換行，多行文字需拆成 Text + Break
    public static Run TextRun(string text, RunProperties? rPr = null)
    {
        var run = new Run();
        if (rPr != null) run.Append(rPr);

        var lines = text.Replace("\r", "").Split('\n');
        for (int i = 0; i < lines.Length; i++)
        {
            if (i > 0) run.Append(new Break());
            run.Append(new Text(lines[i]) { Space = SpaceProcessingModeValues.Preserve });
        }
        return run;
    }
}
