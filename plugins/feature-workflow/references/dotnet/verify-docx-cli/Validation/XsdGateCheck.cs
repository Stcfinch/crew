using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Validation;

namespace FeatureWorkflow.VerifyDocxCli.Validation;

// 用 OpenXML SDK 內建的完整 OOXML schema 驗證產出的 docx 結構。
// 不採用 Core 的 XsdValidator + wml-subset.xsd —— 該 subset 不含 Drawing /
// TOC field / SdtBlock，會把合法元素誤判為非法。
public static class XsdGateCheck
{
    public static bool Check(string docxPath)
    {
        try
        {
            using var doc = WordprocessingDocument.Open(docxPath, false);
            var validator = new OpenXmlValidator(FileFormatVersions.Office2019);
            var errors = validator.Validate(doc).ToList();
            if (errors.Count == 0) return true;

            Console.Error.WriteLine($"[verify-docx-cli] OpenXML 結構驗證失敗：{errors.Count} 個問題");
            foreach (var e in errors.Take(10))
                Console.Error.WriteLine($"  - [{e.Id}] {e.Description}（{e.Path?.XPath}）");
            return false;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"[verify-docx-cli] 結構驗證例外：{ex.Message}");
            return false;
        }
    }
}
