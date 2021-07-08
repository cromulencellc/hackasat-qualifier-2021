


double pow(double value, int exp) {


    int i;
    double result = 1.0;

    for (i=0; i < exp; ++i) {

        result *= value;

    }

    return result;
}