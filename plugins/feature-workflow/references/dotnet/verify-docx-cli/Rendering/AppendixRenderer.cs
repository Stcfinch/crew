using DocumentFormat.OpenXml.Wordprocessing;
using FeatureWorkflow.VerifyDocxCli.Markdown;
using FeatureWorkflow.VerifyDocxCli.Styles;

namespace FeatureWorkflow.VerifyDocxCli.Rendering;

public sealed class AppendixRenderer
{
    private readonly IBrandStyle _style;
    public AppendixRenderer(IBrandStyle style) { _style = style; }

    public void Render(Body body, IReadOnlyList<AppendixVersionEntry> versions)
    {
        body.AppendChild(ParagraphBuilder.Heading("附錄", "Heading1"));
        body.AppendChild(ParagraphBuilder.Heading("版本紀錄", "Heading2"));

        var rows = new List<string[]> { new[] { "日期", "版本", "說明" } };
        foreach (var v in versions)
            rows.Add(new[] { v.Date, v.Version, v.Description });
        body.AppendChild(TableBuilder.BuildSimple(rows.ToArray(), _style));

        body.AppendChild(ParagraphBuilder.Heading("參考文件", "Heading2"));
        body.AppendChild(ParagraphBuilder.Body("- 技術規格書：.spec/{slug}/spec.md"));
        body.AppendChild(ParagraphBuilder.Body("- 驗證技術紀錄：.spec/{slug}/verify.md"));
    }
}
