namespace FeatureWorkflow.VerifyDocxCli;

public static class LogoResolver
{
    public static string? Resolve(string? cliLogo, string styleId)
    {
        // 1. CLI 參數明示
        if (cliLogo != null && File.Exists(cliLogo)) return cliLogo;

        // 2. 使用者覆寫位置
        var userOverride = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
            ".claude", "feature-workflow", "assets", "intumit-logo.png");
        if (File.Exists(userOverride)) return userOverride;

        // 3. Plugin 內建（與 assembly 同目錄的 assets/）
        var assemblyDir = Path.GetDirectoryName(typeof(LogoResolver).Assembly.Location)!;
        var builtin = Path.Combine(assemblyDir, "assets", "intumit-logo.png");
        if (File.Exists(builtin)) return builtin;

        // 4. swiss 不需要 logo → null 合法；其他 style 缺 logo → fail fast
        if (styleId == "swiss") return null;

        throw new FileNotFoundException(
            "找不到 logo。請放置 PNG 到下列任一位置：\n" +
            "  1. --logo {path} CLI 參數\n" +
            $"  2. {userOverride}\n" +
            $"  3. {builtin}");
    }
}
