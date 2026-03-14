/*
 * Decompiled with CFR 0.152.
 */
public class aKQ {
    protected int o;
    protected boolean egk;
    protected String egl;
    protected aKR[] egm;
    protected String egn;
    protected aKT[] ego;

    public int d() {
        return this.o;
    }

    public boolean cjw() {
        return this.egk;
    }

    public String cjx() {
        return this.egl;
    }

    public aKR[] cjy() {
        return this.egm;
    }

    public String cjz() {
        return this.egn;
    }

    public aKT[] cjA() {
        return this.ego;
    }

    public void a(aqH aqH2) {
        int n;
        this.o = aqH2.bGI();
        this.egk = aqH2.bxv();
        this.egl = aqH2.bGL().intern();
        int n2 = aqH2.bGI();
        this.egm = new aKR[n2];
        for (n = 0; n < n2; ++n) {
            this.egm[n] = new aKR();
            this.egm[n].a(aqH2);
        }
        this.egn = aqH2.bGL().intern();
        n = aqH2.bGI();
        this.ego = new aKT[n];
        for (int i = 0; i < n; ++i) {
            this.ego[i] = new aKT();
            this.ego[i].a(aqH2);
        }
    }
}
