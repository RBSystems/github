#include <complex>
#include <map>
#include "stdio.h"
#include "stdlib.h"
#include "string.h"

namespace GFMD_NS {

class CalPhonon: {
    public:
    CalPhonon(int, char **);
    ~CalPhonon();

    void init();
    void setup(int);

    private:
    float kB;
    float T;
    int natom;
    FILE *cellfile;
    FILE *trajfile;
    FILE *fcmatfile;

    void GaussJordan(int, std::complex<double>*);

};
}
