using System.CommandLine;
using System.Text.Json;
using FeatureWorkflow.VerifyDocxCli;
using FeatureWorkflow.VerifyDocxCli.Markdown;
using FeatureWorkflow.VerifyDocxCli.Rendering;
using FeatureWorkflow.VerifyDocxCli.Styles;

var verifyOpt = new Option<FileInfo>("--verify") { Description = "verify.md 路徑", Required = true };
var screenshotsOpt = new Option<DirectoryInfo?>("--screenshots") { Description = "截圖目錄" };
var evidenceOpt = new Option<DirectoryInfo?>("--evidence") { Description = "evidence 目錄" };
var outputOpt = new Option<FileInfo>("--output") { Description = "輸出 docx 路徑", Required = true };
var styleOpt = new Option<string>("--style") { Description = "intumit | tech-dark | swiss", DefaultValueFactory = _ => "intumit" };
styleOpt.AcceptOnlyFromAmong("intumit", "tech-dark", "swiss");
var logoOpt = new Option<FileInfo?>("--logo") { Description = "覆寫 logo 路徑（不給走三層偵測）" };
var coverOpt = new Option<string>("--cover") { Description = "封面資訊 JSON", Required = true };

var root = new RootCommand("verify-docx-cli: 將 verify.md 渲染為品牌 Word 驗收報告");
root.Options.Add(verifyOpt);
root.Options.Add(screenshotsOpt);
root.Options.Add(evidenceOpt);
root.Options.Add(outputOpt);
root.Options.Add(styleOpt);
root.Options.Add(logoOpt);
root.Options.Add(coverOpt);

root.SetAction(parseResult =>
{
    var verify = parseResult.GetValue(verifyOpt)!;
    var output = parseResult.GetValue(outputOpt)!;
    var style = parseResult.GetValue(styleOpt)!;
    var cover = parseResult.GetValue(coverOpt)!;

    Console.WriteLine($"[verify-docx-cli] verify={verify.FullName}");
    Console.WriteLine($"[verify-docx-cli] output={output.FullName}");
    Console.WriteLine($"[verify-docx-cli] style={style}");

    var coverInfo = JsonSerializer.Deserialize<CoverInfo>(cover,
        new JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.CamelCase })!;
    var verifyContent = File.ReadAllText(verify.FullName);
    var report = VerifyMarkdownParser.Parse(verifyContent, coverInfo);

    Console.WriteLine($"[verify-docx-cli] 解析完成: {report.Details.Count} 個驗收項目, {report.Pending.Count} 個待處理");

    var logoPath = LogoResolver.Resolve(parseResult.GetValue(logoOpt)?.FullName, style);
    new DocumentBuilder().Build(report, BrandStyleFactory.Resolve(style),
        logoPath, parseResult.GetValue(screenshotsOpt), parseResult.GetValue(evidenceOpt), output);

    Console.WriteLine($"[verify-docx-cli] ✅ 已產出 {output.FullName}");

    if (!FeatureWorkflow.VerifyDocxCli.Validation.XsdGateCheck.Check(output.FullName))
    {
        Console.Error.WriteLine("[verify-docx-cli] ⚠️  docx 已產出但結構驗證失敗，請檢查上方錯誤訊息");
        return 1;
    }
    Console.WriteLine("[verify-docx-cli] ✅ 結構驗證通過");
    return 0;
});

return await root.Parse(args).InvokeAsync();
