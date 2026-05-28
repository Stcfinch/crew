using DocumentFormat.OpenXml.Wordprocessing;
using FeatureWorkflow.VerifyDocxCli.Markdown;
using FeatureWorkflow.VerifyDocxCli.Styles;

namespace FeatureWorkflow.VerifyDocxCli.Rendering;

public sealed class EnvRenderer
{
    private readonly IBrandStyle _style;
    public EnvRenderer(IBrandStyle style) { _style = style; }

    public void Render(Body body, EnvInfo env)
    {
        body.AppendChild(ParagraphBuilder.Heading("測試環境", "Heading1"));
        body.AppendChild(TableBuilder.BuildSimple(new[]
        {
            new[] { "項目", "說明" },
            new[] { "測試 URL", env.Url },
            new[] { "瀏覽器", env.Browser },
            new[] { "測試帳號角色", env.Role },
            new[] { "測試資料說明", env.DataDescription },
            new[] { "前置條件", env.Prerequisites },
        }, _style));
    }
}
