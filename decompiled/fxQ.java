/*
 * Decompiled with CFR 0.152.
 */
public class fxQ {
    protected int cxt;
    protected fxR[] tBm;
    protected int tBn;
    protected fxS[] tBo;

    public int wp() {
        return this.cxt;
    }

    public fxR[] gqe() {
        return this.tBm;
    }

    public int gqf() {
        return this.tBn;
    }

    public fxS[] gqg() {
        return this.tBo;
    }

    public void a(aqH aqH2) {
        int n;
        this.cxt = aqH2.bGI();
        int n2 = aqH2.bGI();
        this.tBm = new fxR[n2];
        for (n = 0; n < n2; ++n) {
            this.tBm[n] = new fxR();
            ((fxr)this.tBm[n]).a(aqH2);
        }
        this.tBn = aqH2.bGI();
        n = aqH2.bGI();
        this.tBo = new fxS[n];
        for (int i = 0; i < n; ++i) {
            this.tBo[i] = new fxS();
            this.tBo[i].a(aqH2);
        }
    }
}
