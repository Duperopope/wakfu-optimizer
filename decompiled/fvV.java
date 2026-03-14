/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fvV
implements aqz {
    protected int o;
    protected short ekU;
    protected int ejx;
    protected int ekV;
    protected byte ekW;
    protected byte ekX;
    protected int ekY;
    protected boolean biy;
    protected fvW[] tzy;
    protected fvX[] tzz;
    protected int[] egL;
    protected fvY[] tzA;

    public int d() {
        return this.o;
    }

    public short coj() {
        return this.ekU;
    }

    public int cmP() {
        return this.ejx;
    }

    public int cok() {
        return this.ekV;
    }

    public byte col() {
        return this.ekW;
    }

    public byte com() {
        return this.ekX;
    }

    public int conn() {
        return this.ekY;
    }

    public boolean ckf() {
        return this.biy;
    }

    public fvW[] gos() {
        return this.tzy;
    }

    public fvX[] got() {
        return this.tzz;
    }

    public int[] cjX() {
        return this.egL;
    }

    public fvY[] gou() {
        return this.tzA;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.ekU = 0;
        this.ejx = 0;
        this.ekV = 0;
        this.ekW = 0;
        this.ekX = 0;
        this.ekY = 0;
        this.biy = false;
        this.tzy = null;
        this.tzz = null;
        this.egL = null;
        this.tzA = null;
    }

    @Override
    public void a(aqH aqH2) {
        int n;
        int n2;
        this.o = aqH2.bGI();
        this.ekU = aqH2.bGG();
        this.ejx = aqH2.bGI();
        this.ekV = aqH2.bGI();
        this.ekW = aqH2.aTf();
        this.ekX = aqH2.aTf();
        this.ekY = aqH2.bGI();
        this.biy = aqH2.bxv();
        int n3 = aqH2.bGI();
        this.tzy = new fvW[n3];
        for (n2 = 0; n2 < n3; ++n2) {
            this.tzy[n2] = new fvW();
            this.tzy[n2].a(aqH2);
        }
        n2 = aqH2.bGI();
        this.tzz = new fvX[n2];
        for (n = 0; n < n2; ++n) {
            this.tzz[n] = new fvX();
            this.tzz[n].a(aqH2);
        }
        this.egL = aqH2.bGM();
        n = aqH2.bGI();
        this.tzA = new fvY[n];
        for (int i = 0; i < n; ++i) {
            this.tzA[i] = new fvY();
            ((fvy)this.tzA[i]).a(aqH2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.oAn.d();
    }
}
