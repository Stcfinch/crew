namespace FeatureWorkflow.VerifyDocxCli.Styles;

public sealed class SwissStyle : IBrandStyle
{
    public string Id => "swiss";
    public bool ShowLogo => false;
    public string TitleColor => BrandColors.SwissBlack;
    public string AccentColor => BrandColors.SwissGray;
    public string TableHeaderBg => "EEEEEE";
    public string TableHeaderFg => BrandColors.SwissBlack;
    public string LatinFont => "Helvetica Neue";
    public string CjkFont => "Microsoft JhengHei";
    public string CoverDecorationHint => "none";
}
