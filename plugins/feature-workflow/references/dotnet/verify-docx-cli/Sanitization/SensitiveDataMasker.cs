namespace FeatureWorkflow.VerifyDocxCli.Sanitization;

public static class SensitiveDataMasker
{
    public static Dictionary<string, string> Mask(IReadOnlyDictionary<string, string> headers)
    {
        var result = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        foreach (var (k, v) in headers)
        {
            result[k] = k.ToLowerInvariant() switch
            {
                "cookie"        => MaskCookie(v),
                "authorization" => MaskAuthorization(v),
                "x-api-key"     => MaskShortToken(v),
                "x-token"       => MaskShortToken(v),
                _ => v
            };
        }
        return result;
    }

    private static string MaskCookie(string v) =>
        v.Length <= 8 ? "****" : $"{v[..4]}****{v[^4..]}";

    private static string MaskAuthorization(string v)
    {
        var parts = v.Split(' ', 2);
        if (parts.Length < 2) return MaskShortToken(v);
        var scheme = parts[0];
        var token = parts[1];
        return token.Length <= 4 ? $"{scheme} ****" : $"{scheme} {token[..4]}****";
    }

    private static string MaskShortToken(string v) =>
        v.Length <= 4 ? "****" : $"{v[..4]}****";
}
