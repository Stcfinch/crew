namespace FeatureWorkflow.VerifyDocxCli.Styles;

public sealed class IntumitStyle : IBrandStyle
{
    public string Id => "intumit";
    public bool ShowLogo => true;
    public string TitleColor => BrandColors.IntumitBlue;
    public string AccentColor => BrandColors.IntumitOrange;
    public string TableHeaderBg => BrandColors.IntumitBlue;
    public string TableHeaderFg => "FFFFFF";
    public string LatinFont => "Calibri";
    public string CjkFont => "Microsoft JhengHei"; // 微軟正黑體
    public string CoverDecorationHint => "orange-line";
}
