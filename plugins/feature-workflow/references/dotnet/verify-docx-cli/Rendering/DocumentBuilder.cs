using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;
using FeatureWorkflow.VerifyDocxCli.Markdown;
using FeatureWorkflow.VerifyDocxCli.Styles;

namespace FeatureWorkflow.VerifyDocxCli.Rendering;

public sealed class DocumentBuilder
{
    public void Build(VerifyReport report, IBrandStyle style, string? logoPath,
        DirectoryInfo? screenshotsDir, DirectoryInfo? evidenceDir, FileInfo outputFile)
    {
        using var doc = WordprocessingDocument.Create(outputFile.FullName,
            WordprocessingDocumentType.Document);

        var mainPart = doc.AddMainDocumentPart();
        mainPart.Document = new Document(new Body());
        var body = mainPart.Document.Body!;

        // 樣式定義（Heading OutlineLevel 是 TOC 必需）
        StyleRegistrar.Register(mainPart, style);

        // 開檔時自動提示更新功能變數（TOC 才會填值）
        var settingsPart = mainPart.AddNewPart<DocumentSettingsPart>();
        settingsPart.Settings = new Settings(new UpdateFieldsOnOpen { Val = true });

        new CoverRenderer(mainPart, style, logoPath).Render(body, report.Cover);
        new SignoffRenderer(style).Render(body, report.Cover.Author);
        TocInserter.Insert(body);
        new EnvRenderer(style).Render(body, report.Env);
        new SummaryRenderer(style).Render(body, report.Summary);
        new DetailRenderer(mainPart, style, screenshotsDir, evidenceDir).Render(body, report.Details);
        if (report.Pending.Count > 0)
            new PendingRenderer(style).Render(body, report.Pending);
        new AppendixRenderer(style).Render(body, report.Versions);

        // body 最後一個 child 必須是 sectPr
        body.AppendChild(new SectionProperties(
            new PageSize { Width = 11906U, Height = 16838U },
            new PageMargin
            {
                Top = 1440, Bottom = 1440, Left = 1440, Right = 1440,
                Header = 720U, Footer = 720U, Gutter = 0U
            }));
    }
}
