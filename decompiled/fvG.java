/*
 * Decompiled with CFR 0.152.
 */
public class fvG {
    protected int ejX;
    protected String eik;
    protected fvF[] tzr;
    protected int ejZ;
    protected int eka;
    protected fvH[] tzs;
    protected int ekc;

    public int cnm() {
        return this.ejX;
    }

    public String clB() {
        return this.eik;
    }

    public fvF[] gol() {
        return this.tzr;
    }

    public int cno() {
        return this.ejZ;
    }

    public int cnp() {
        return this.eka;
    }

    public fvH[] gom() {
        return this.tzs;
    }

    public int cnr() {
        return this.ekc;
    }

    public void a(aqH aqH2) {
        int n;
        this.ejX = aqH2.bGI();
        this.eik = aqH2.bGL().intern();
        int n2 = aqH2.bGI();
        this.tzr = new fvF[n2];
        for (n = 0; n < n2; ++n) {
            this.tzr[n] = new fvF();
            this.tzr[n].a(aqH2);
        }
        this.ejZ = aqH2.bGI();
        this.eka = aqH2.bGI();
        n = aqH2.bGI();
        this.tzs = new fvH[n];
        for (int i = 0; i < n; ++i) {
            this.tzs[i] = new fvH();
            ((fvh)this.tzs[i]).a(aqH2);
        }
        this.ekc = aqH2.bGI();
    }
}
