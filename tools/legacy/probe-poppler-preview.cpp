#include "GlobalParams.h"
#include "PDFDoc.h"
#include "SplashOutputDev.h"
#include "splash/SplashBitmap.h"
#include "goo/GooString.h"
#include <memory>

int main(int argc, char **argv) {
    if (argc != 4) return 2;
    globalParams = std::make_unique<GlobalParams>(argv[2]);
    // Poppler 21 takes ownership of this filename pointer.
    PDFDoc doc(new GooString(argv[1]));
    if (!doc.isOk()) return 3;
    SplashColor paper = {255,255,255};
    SplashOutputDev output(splashModeRGB8, 4, false, paper);
    output.startDoc(&doc);
    doc.displayPage(&output, 1, 96, 96, 0, false, true, false);
    return output.getBitmap()->writePNMFile(argv[3]);
}
