#include <PID_v1.h>

class Controller : public PID
{
    public:
    Controller(*PID);
    int Method1(int, int);
    int c;
};