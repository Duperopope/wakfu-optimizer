/*
 * Decompiled with CFR 0.152.
 */
public class fxy {
    protected int eqo;
    protected int eqp;
    protected int ekY;
    protected int bap;
    protected int baq;
    protected byte eqq;
    protected fxz[] tAZ;

    public int ctR() {
        return this.eqo;
    }

    public int ctS() {
        return this.eqp;
    }

    public int conn() {
        return this.ekY;
    }

    public int getX() {
        return this.bap;
    }

    public int getY() {
        return this.baq;
    }

    public byte ctT() {
        return this.eqq;
    }

    public fxz[] gpS() {
        return this.tAZ;
    }

    public void a(aqH aqH2) {
        this.eqo = aqH2.bGI();
        this.eqp = aqH2.bGI();
        this.ekY = aqH2.bGI();
        this.bap = aqH2.bGI();
        this.baq = aqH2.bGI();
        this.eqq = aqH2.aTf();
        int n = aqH2.bGI();
        this.tAZ = new fxz[n];
        for (int i = 0; i < n; ++i) {
            this.tAZ[i] = new fxz();
            this.tAZ[i].a(aqH2);
        }
    }
}
