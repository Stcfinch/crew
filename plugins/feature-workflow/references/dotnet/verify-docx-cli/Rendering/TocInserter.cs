using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Wordprocessing;

namespace FeatureWorkflow.VerifyDocxCli.Rendering;

public static class TocInserter
{
    // 插入「目錄」標題 + TOC complex field。
    // DocumentBuilder 已設 UpdateFieldsOnOpen，Word 開檔會提示更新目錄。
    public static void Insert(Body body)
    {
        body.AppendChild(ParagraphBuilder.Heading("目錄", "Heading1"));

        var p = new Paragraph();
        p.AppendChild(new Run(new FieldChar { FieldCharType = FieldCharValues.Begin }));
        p.AppendChild(new Run(new FieldCode(@" TOC \o ""1-3"" \h \z \u ")
        { Space = SpaceProcessingModeValues.Preserve }));
        p.AppendChild(new Run(new FieldChar { FieldCharType = FieldCharValues.Separate }));
        p.AppendChild(new Run(new Text("(請在 Word 開啟後按 F9 或右鍵『更新功能變數』來填入目錄)")));
        p.AppendChild(new Run(new FieldChar { FieldCharType = FieldCharValues.End }));
        body.AppendChild(p);

        body.AppendChild(new Paragraph(new Run(new Break { Type = BreakValues.Page })));
    }
}
