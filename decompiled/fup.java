/*
 * Decompiled with CFR 0.152.
 */
public class fup {
    protected int o;
    protected String egl;
    protected fuq[] tyv;
    protected fus[] tyw;
    protected fuo[] tyx;

    public int d() {
        return this.o;
    }

    public String cjx() {
        return this.egl;
    }

    public fuq[] gno() {
        return this.tyv;
    }

    public fus[] gnp() {
        return this.tyw;
    }

    public fuo[] gnq() {
        return this.tyx;
    }

    public void a(aqH aqH2) {
        int n;
        int n2;
        this.o = aqH2.bGI();
        this.egl = aqH2.bGL().intern();
        int n3 = aqH2.bGI();
        this.tyv = new fuq[n3];
        for (n2 = 0; n2 < n3; ++n2) {
            this.tyv[n2] = new fuq();
            ((fuQ)this.tyv[n2]).a(aqH2);
        }
        n2 = aqH2.bGI();
        this.tyw = new fus[n2];
        for (n = 0; n < n2; ++n) {
            this.tyw[n] = new fus();
            this.tyw[n].a(aqH2);
        }
        n = aqH2.bGI();
        this.tyx = new fuo[n];
        for (int i = 0; i < n; ++i) {
            this.tyx[i] = new fuo();
            this.tyx[i].a(aqH2);
        }
    }
}
