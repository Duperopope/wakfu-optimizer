/*
 * Decompiled with CFR 0.152.
 */
public class fxD {
    protected int eqv;
    protected byte eqq;
    protected byte eqw;
    protected fxE[] tBc;

    public int ctY() {
        return this.eqv;
    }

    public byte ctT() {
        return this.eqq;
    }

    public byte ctZ() {
        return this.eqw;
    }

    public fxE[] gpV() {
        return this.tBc;
    }

    public void a(aqH aqH2) {
        this.eqv = aqH2.bGI();
        this.eqq = aqH2.aTf();
        this.eqw = aqH2.aTf();
        int n = aqH2.bGI();
        this.tBc = new fxE[n];
        for (int i = 0; i < n; ++i) {
            this.tBc[i] = new fxE();
            ((fxe)this.tBc[i]).a(aqH2);
        }
    }
}
