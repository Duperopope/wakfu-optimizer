/*
 * Decompiled with CFR 0.152.
 */
public class fvP {
    protected int o;
    protected int ehO;
    protected int eky;
    protected int ekz;
    protected boolean ekA;
    protected int ejx;
    protected int ekB;
    protected fvO[] tzw;

    public int d() {
        return this.o;
    }

    public int clf() {
        return this.ehO;
    }

    public int cnM() {
        return this.eky;
    }

    public int cnN() {
        return this.ekz;
    }

    public boolean cnO() {
        return this.ekA;
    }

    public int cmP() {
        return this.ejx;
    }

    public int cnP() {
        return this.ekB;
    }

    public fvO[] goq() {
        return this.tzw;
    }

    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.ehO = aqH2.bGI();
        this.eky = aqH2.bGI();
        this.ekz = aqH2.bGI();
        this.ekA = aqH2.bxv();
        this.ejx = aqH2.bGI();
        this.ekB = aqH2.bGI();
        int n = aqH2.bGI();
        this.tzw = new fvO[n];
        for (int i = 0; i < n; ++i) {
            this.tzw[i] = new fvO();
            ((fvo)this.tzw[i]).a(aqH2);
        }
    }
}
