using DocumentFormat.OpenXml.Wordprocessing;
using FeatureWorkflow.VerifyDocxCli.Styles;

namespace FeatureWorkflow.VerifyDocxCli.Rendering;

public sealed class SignoffRenderer
{
    private readonly IBrandStyle _style;
    public SignoffRenderer(IBrandStyle style) { _style = style; }

    public void Render(Body body, string defaultAuthor)
    {
        body.AppendChild(ParagraphBuilder.Heading("簽核", "Heading1"));
        body.AppendChild(TableBuilder.BuildSimple(new[]
        {
            new[] { "角色", "姓名", "簽章", "日期" },
            new[] { "製作人", defaultAuthor, "", "" },
            new[] { "審核人", "", "", "" },
            new[] { "客戶確認", "", "", "" },
        }, _style));
    }
}
