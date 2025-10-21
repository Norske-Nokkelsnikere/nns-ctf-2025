#include <zephyr/kernel.h>
#include "tommath.h"
#include <zephyr/console/console.h>

mp_err modpow(mp_int *base, mp_int *exp, mp_int *mod, mp_int *result)
{
    mp_err rtn = mp_init_i32(result, 1);
    if (rtn != MP_OKAY)
    {
        return rtn;
    }

    while (!mp_iszero(exp)) {
        if (mp_isodd(exp)) {
            rtn = mp_mul(result, base, result);
            if (rtn != MP_OKAY)
            {
                return rtn;
            }

            rtn = mp_mod(result, mod, result);
            if (rtn != MP_OKAY)
            {
                return rtn;
            }
        }

        rtn = mp_div_2d(exp, 1, exp, NULL);
        if (rtn != MP_OKAY)
        {
            return rtn;
        }

        rtn = mp_mul(base, base, base);
        if (rtn != MP_OKAY)
        {
            return rtn;
        }
        
        rtn = mp_mod(base, mod, base);
        if (rtn != MP_OKAY)
        {
            return rtn;
        }

        k_sleep(K_MSEC(3));
    }

    return rtn;
}

int main(void)
{
    printk("Loading parameters.\n");

    mp_int n, d, c, m;
    mp_err res = mp_init(&n);
    if (res != MP_OKAY)
    {
        printk("Failed to initialise n: %d\n", res  );
        return -1;
    }

    res = mp_init(&d);
    if (res != MP_OKAY)
    {
        printk("Failed to initialise d: %d\n", res  );
        return -1;
    }

    res = mp_init(&c);
    if (res != MP_OKAY)
    {
        printk("Failed to initialise c: %d\n", res  );
        return -1;
    }

    res = mp_init(&m);
    if (res != MP_OKAY)
    {
        printk("Failed to initialise m: %d\n", res  );
        return -1;
    }

    const char* n_value = "13664239037907372261661891470992995812128631528934391124752884269617528651053943317643090937575784947507121014497497717171715238000721198283113013794512130295734489576260331261682561465391758930638013357402072021478110973654128826298049766903982395037335779141190402313347639858098129949466177493850907993591446653720099179365990534644620448650304131652280474041746240378613910471399168587342852511744545430231691608897504605714598606184911482705356693806768783646940958690855586096924000403615689800819397967604105338773209636756859376501323800107361614560297027162314856937948699650209286373343705091388728140792503";
    const char* d_value = "12198091229576740073066038428833257854167654723290760223288638390435532809404015347036163316948766320611320551034928421244963913502787642180043744328363095395760353886493288988887777263724992847353052038921650725797288287740281169149753598924538657882712509859397660670192466391473993205266013309699061174070432094598535333579917667263399538234730654655537369432047613126791256261606793368850292163333825769255762791425188947388031692719299335721791332391141486126631359462561172369363255266063706380761596896212041948116306369754039933523443196076399014502547063755298283128496407449100124937750247618124928598785593";
    const char* c_value = "7017475957803874462523966074302543158129097147429790657226279960682896591477226122698282095738274246721238318890653196205916830216637458496892522095257681715003618677124495890023843861343165641630855514175553150271337745667046395825325665199881603875814091318619655247836156484392842577721656378956876207867313374046749934094115294456504848029102891923490159831053984238123331848687881208689685500800642357139091392163908410372967220411143432404551854426595259687401994837786183518387073808919815886349474945163639093802074478297811137406107429230463524738469120697169759618786129980489550678589429921447071806277046";

    res = mp_read_radix(&n, n_value, 10);
    if (res != MP_OKAY)
    {
        printk("Failed to read n: %d\n", res);
        return -1;
    }

    res = mp_read_radix(&d, d_value, 10);
    if (res != MP_OKAY)
    {
        printk("Failed to read d: %d\n", res);
        return -1;
    }

    res = mp_read_radix(&c, c_value, 10);
    if (res != MP_OKAY)
    {
        printk("Failed to read c: %d\n", res);
        return -1;
    }

    k_sleep(K_MSEC(100));

    res = modpow(&c, &d, &n, &m);
    if (res != MP_OKAY)
    {
        printk("Failed to compute m: %d\n", res);
        return -1;
    }

    k_sleep(K_MSEC(100));

    char flag[40];

    for (int i = 0; !mp_iszero(&m); i++)
    {
        flag[i] = mp_get_i32(&m) & 0xFF;
        res = mp_div_2d(&m, 8, &m, NULL);
        if (res != MP_OKAY)
        {
            printk("Failed to shift m: %d\n", res);
            return -1;
        }

        flag[i + 1] = '\0'; // Null-terminate the string
    }
    printk("Flag loaded\n\n");

    printk("Welcome to the ultra low power flag checker!\nPlease provide flag for validation\n\n");
    
    console_getline_init();

    while (1)
    {
        printk("Flag: ");

        char* user_input = console_getline();

        if (!user_input || strcmp(user_input, flag))
        {
            printk("Wrong flag! Try again.\n");
        }
        else
        {
            printk("Correct flag! Well done!\n");
            break;
        }
    }
}
