// Image helpers used by build-images.ps1 (compiled at runtime with Add-Type).
// Originals in "Initial Images" are never modified; all output goes to assets/.
using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
using System.Linq;

public static class ImageTools
{
    static ImageCodecInfo Jpeg = ImageCodecInfo.GetImageEncoders().First(c => c.MimeType == "image/jpeg");

    public static Bitmap Load(string path, int x, int y, int w, int h)
    {
        using (var src = Image.FromFile(path))
        {
            if (w <= 0) { x = 0; y = 0; w = src.Width; h = src.Height; }
            var bmp = new Bitmap(w, h, PixelFormat.Format24bppRgb);
            using (var g = Graphics.FromImage(bmp))
            {
                g.DrawImage(src, new Rectangle(0, 0, w, h), new Rectangle(x, y, w, h), GraphicsUnit.Pixel);
            }
            return bmp;
        }
    }

    // Resize to target width (never upscales) and save as progressive-quality JPEG.
    public static string SaveJpeg(Bitmap src, string outPath, int width, long quality)
    {
        if (width > src.Width) width = src.Width;
        int height = (int)Math.Round(src.Height * (double)width / src.Width);
        using (var dst = new Bitmap(width, height, PixelFormat.Format24bppRgb))
        {
            using (var g = Graphics.FromImage(dst))
            {
                g.InterpolationMode = InterpolationMode.HighQualityBicubic;
                g.PixelOffsetMode = PixelOffsetMode.HighQuality;
                g.SmoothingMode = SmoothingMode.HighQuality;
                g.CompositingQuality = CompositingQuality.HighQuality;
                using (var wrap = new ImageAttributes())
                {
                    wrap.SetWrapMode(WrapMode.TileFlipXY); // avoids dark edge halos
                    g.DrawImage(src, new Rectangle(0, 0, width, height), 0, 0, src.Width, src.Height, GraphicsUnit.Pixel, wrap);
                }
            }
            var p = new EncoderParameters(1);
            p.Param[0] = new EncoderParameter(Encoder.Quality, quality);
            dst.Save(outPath, Jpeg, p);
        }
        return width + "x" + height;
    }

    // Bounding box of non-white pixels (threshold on max channel distance from white).
    public static Rectangle ContentBox(Bitmap b, int threshold)
    {
        int minX = b.Width, minY = b.Height, maxX = -1, maxY = -1;
        for (int y = 0; y < b.Height; y++)
            for (int x = 0; x < b.Width; x++)
            {
                var c = b.GetPixel(x, y);
                int d = 255 - Math.Min(c.R, Math.Min(c.G, c.B));
                if (d > threshold) { if (x < minX) minX = x; if (x > maxX) maxX = x; if (y < minY) minY = y; if (y > maxY) maxY = y; }
            }
        return new Rectangle(minX, minY, maxX - minX + 1, maxY - minY + 1);
    }

    // GIMP-style "color to alpha" against white: removes the white background
    // while preserving the logo's exact colours on any light surface.
    public static Bitmap WhiteToAlpha(Bitmap src)
    {
        var dst = new Bitmap(src.Width, src.Height, PixelFormat.Format32bppArgb);
        for (int y = 0; y < src.Height; y++)
            for (int x = 0; x < src.Width; x++)
            {
                var c = src.GetPixel(x, y);
                double r = c.R / 255.0, g = c.G / 255.0, bl = c.B / 255.0;
                double a = Math.Max(Math.Max(1 - r, 1 - g), 1 - bl);
                if (a < 0.03) { dst.SetPixel(x, y, Color.FromArgb(0, 255, 255, 255)); continue; }
                Func<double, int> un = v => (int)Math.Round(Math.Max(0, Math.Min(1, (v - 1) / a + 1)) * 255);
                dst.SetPixel(x, y, Color.FromArgb((int)Math.Round(a * 255), un(r), un(g), un(bl)));
            }
        return dst;
    }

    public static Bitmap CropArgb(Bitmap src, Rectangle r)
    {
        var dst = new Bitmap(r.Width, r.Height, PixelFormat.Format32bppArgb);
        using (var g = Graphics.FromImage(dst)) g.DrawImage(src, new Rectangle(0, 0, r.Width, r.Height), r, GraphicsUnit.Pixel);
        return dst;
    }

    public static void SavePngScaled(Bitmap src, string outPath, int width)
    {
        int height = (int)Math.Round(src.Height * (double)width / src.Width);
        using (var dst = new Bitmap(width, height, PixelFormat.Format32bppArgb))
        {
            using (var g = Graphics.FromImage(dst))
            {
                g.InterpolationMode = InterpolationMode.HighQualityBicubic;
                g.PixelOffsetMode = PixelOffsetMode.HighQuality;
                g.DrawImage(src, 0, 0, width, height);
            }
            dst.Save(outPath, ImageFormat.Png);
        }
    }

    // Square icon: the logo mark centred on a solid ivory tile with padding.
    public static void SaveIcon(Bitmap mark, string outPath, int size, Color bg, double pad, bool round)
    {
        using (var dst = new Bitmap(size, size, PixelFormat.Format32bppArgb))
        {
            using (var g = Graphics.FromImage(dst))
            {
                g.SmoothingMode = SmoothingMode.AntiAlias;
                g.InterpolationMode = InterpolationMode.HighQualityBicubic;
                g.PixelOffsetMode = PixelOffsetMode.HighQuality;
                g.Clear(Color.Transparent);
                using (var br = new SolidBrush(bg))
                {
                    if (round)
                    {
                        int rad = size / 5;
                        var path = new GraphicsPath();
                        path.AddArc(0, 0, rad * 2, rad * 2, 180, 90);
                        path.AddArc(size - rad * 2 - 1, 0, rad * 2, rad * 2, 270, 90);
                        path.AddArc(size - rad * 2 - 1, size - rad * 2 - 1, rad * 2, rad * 2, 0, 90);
                        path.AddArc(0, size - rad * 2 - 1, rad * 2, rad * 2, 90, 90);
                        path.CloseFigure();
                        g.FillPath(br, path);
                    }
                    else g.FillRectangle(br, 0, 0, size, size);
                }
                double avail = size * (1 - 2 * pad);
                double s = Math.Min(avail / mark.Width, avail / mark.Height);
                int w = (int)Math.Round(mark.Width * s), h = (int)Math.Round(mark.Height * s);
                g.DrawImage(mark, (size - w) / 2, (size - h) / 2, w, h);
            }
            dst.Save(outPath, ImageFormat.Png);
        }
    }

    // 1200x630 sharing image: real resort photo on the right, ivory panel with the logo on the left.
    public static void SaveShareImage(string photoPath, Rectangle photoCrop, Bitmap logo, string outPath)
    {
        using (var photo = Load(photoPath, photoCrop.X, photoCrop.Y, photoCrop.Width, photoCrop.Height))
        using (var dst = new Bitmap(1200, 630, PixelFormat.Format24bppRgb))
        {
            using (var g = Graphics.FromImage(dst))
            {
                g.InterpolationMode = InterpolationMode.HighQualityBicubic;
                g.PixelOffsetMode = PixelOffsetMode.HighQuality;
                g.SmoothingMode = SmoothingMode.AntiAlias;
                g.Clear(Color.FromArgb(0xEE, 0xE8, 0xDA));
                g.DrawImage(photo, new Rectangle(500, 0, 700, 630));
                double s = 380.0 / logo.Width;
                int lw = 380, lh = (int)Math.Round(logo.Height * s);
                g.DrawImage(logo, 60, (630 - lh) / 2, lw, lh);
                using (var pen = new Pen(Color.FromArgb(0x73, 0xBC, 0xBF), 4)) g.DrawLine(pen, 500, 0, 500, 630);
            }
            var p = new EncoderParameters(1);
            p.Param[0] = new EncoderParameter(Encoder.Quality, 88L);
            dst.Save(outPath, Jpeg, p);
        }
    }
}
