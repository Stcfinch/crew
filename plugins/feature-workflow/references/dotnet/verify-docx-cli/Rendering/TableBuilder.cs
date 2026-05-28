using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Wordprocessing;
using FeatureWorkflow.VerifyDocxCli.Styles;

namespace FeatureWorkflow.VerifyDocxCli.Rendering;

public static class TableBuilder
{
    // A4 1 吋邊界下可用寬度約 9026 DXA
    private const int UsableWidthDxa = 9026;

    public static Table BuildSimple(string[][] rows, IBrandStyle style, bool firstRowIsHeader = true)
    {
        var table = new Table();
        int cols = rows.Length > 0 ? rows[0].Length : 1;
        int colWidth = UsableWidthDxa / Math.Max(cols, 1);

        table.AppendChild(new TableProperties(
            new TableWidth { Width = "5000", Type = TableWidthUnitValues.Pct },
            BuildBorders()));

        var grid = new TableGrid();
        for (int i = 0; i < cols; i++)
            grid.AppendChild(new GridColumn { Width = colWidth.ToString() });
        table.AppendChild(grid);

        for (int r = 0; r < rows.Length; r++)
        {
            bool isHeader = firstRowIsHeader && r == 0;
            var row = new TableRow();
            foreach (var cellText in rows[r])
                row.AppendChild(BuildCell(cellText, isHeader, colWidth, style));
            table.AppendChild(row);
        }
        return table;
    }

    private static TableCell BuildCell(string text, bool isHeader, int widthDxa, IBrandStyle style)
    {
        var tcPr = new TableCellProperties(
            new TableCellWidth { Width = widthDxa.ToString(), Type = TableWidthUnitValues.Dxa });
        if (isHeader)
            tcPr.AppendChild(new Shading
            {
                Val = ShadingPatternValues.Clear,
                Color = "auto",
                Fill = style.TableHeaderBg
            });

        RunProperties? rPr = null;
        if (isHeader)
            rPr = new RunProperties(new Bold(), new Color { Val = style.TableHeaderFg });

        return new TableCell(tcPr, new Paragraph(ParagraphBuilder.TextRun(text, rPr)));
    }

    private static TableBorders BuildBorders()
    {
        UInt32Value size = 4U;
        // CT_TblBorders sequence: top, left, bottom, right, insideH, insideV
        return new TableBorders(
            new TopBorder { Val = BorderValues.Single, Size = size, Color = "BFBFBF" },
            new LeftBorder { Val = BorderValues.Single, Size = size, Color = "BFBFBF" },
            new BottomBorder { Val = BorderValues.Single, Size = size, Color = "BFBFBF" },
            new RightBorder { Val = BorderValues.Single, Size = size, Color = "BFBFBF" },
            new InsideHorizontalBorder { Val = BorderValues.Single, Size = size, Color = "BFBFBF" },
            new InsideVerticalBorder { Val = BorderValues.Single, Size = size, Color = "BFBFBF" });
    }
}
