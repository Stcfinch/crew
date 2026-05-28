namespace FeatureWorkflow.VerifyDocxCli.Styles;

public interface IBrandStyle
{
    string Id { get; }                  // "intumit" | "tech-dark" | "swiss"
    bool ShowLogo { get; }              // swiss = false
    string TitleColor { get; }          // hex
    string AccentColor { get; }
    string TableHeaderBg { get; }
    string TableHeaderFg { get; }
    string LatinFont { get; }           // 西文字型
    string CjkFont { get; }             // 中文字型
    string CoverDecorationHint { get; } // 給 CoverRenderer 用：「orange-line」「code-bar」「none」
}

public static class BrandStyleFactory
{
    public static IBrandStyle Resolve(string id) => id switch
    {
        "intumit"   => new IntumitStyle(),
        "tech-dark" => new TechDarkStyle(),
        "swiss"     => new SwissStyle(),
        _ => throw new ArgumentException($"未知 style: {id}（可用：intumit | tech-dark | swiss）")
    };
}
