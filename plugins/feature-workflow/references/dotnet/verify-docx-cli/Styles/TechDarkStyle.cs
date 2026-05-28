namespace FeatureWorkflow.VerifyDocxCli.Styles;

public sealed class TechDarkStyle : IBrandStyle
{
    public string Id => "tech-dark";
    public bool ShowLogo => true;
    public string TitleColor => BrandColors.TechDarkAccent;
    public string AccentColor => BrandColors.TechDarkAccent;
    public string TableHeaderBg => BrandColors.TechDarkBg;
    public string TableHeaderFg => BrandColors.TechDarkAccent;
    public string LatinFont => "Consolas";
    public string CjkFont => "Microsoft JhengHei";
    public string CoverDecorationHint => "code-bar";
}
