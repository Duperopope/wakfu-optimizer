/*
 * Decompiled with CFR 0.152.
 */
public class aOr {
    protected int cxt;
    protected aOs[] erg;
    protected int erh;
    protected int eri;
    protected int erj;
    protected int erk;
    protected int cDu;
    protected int erl;

    public int wp() {
        return this.cxt;
    }

    public aOs[] cuI() {
        return this.erg;
    }

    public int cuJ() {
        return this.erh;
    }

    public int cuK() {
        return this.eri;
    }

    public int cuL() {
        return this.erj;
    }

    public int cuM() {
        return this.erk;
    }

    public int bBE() {
        return this.cDu;
    }

    public int cuN() {
        return this.erl;
    }

    public void a(aqH aqH2) {
        this.cxt = aqH2.bGI();
        int n = aqH2.bGI();
        this.erg = new aOs[n];
        for (int i = 0; i < n; ++i) {
            this.erg[i] = new aOs();
            ((aOS)this.erg[i]).a(aqH2);
        }
        this.erh = aqH2.bGI();
        this.eri = aqH2.bGI();
        this.erj = aqH2.bGI();
        this.erk = aqH2.bGI();
        this.cDu = aqH2.bGI();
        this.erl = aqH2.bGI();
    }
}
