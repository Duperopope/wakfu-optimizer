/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aOE
implements aqz {
    protected int o;
    protected int ehO;
    protected boolean etV;
    protected String etW;
    protected aOG[] etX;
    protected aOG[] etY;
    protected aOF[] etZ;
    protected aOH[] eua;
    protected aOI[] eub;

    public int d() {
        return this.o;
    }

    public int clf() {
        return this.ehO;
    }

    public boolean cxF() {
        return this.etV;
    }

    public String cxG() {
        return this.etW;
    }

    public aOG[] cxH() {
        return this.etX;
    }

    public aOG[] cxI() {
        return this.etY;
    }

    public aOF[] cxJ() {
        return this.etZ;
    }

    public aOH[] cxK() {
        return this.eua;
    }

    public aOI[] cxL() {
        return this.eub;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.ehO = 0;
        this.etV = false;
        this.etW = null;
        this.etX = null;
        this.etY = null;
        this.etZ = null;
        this.eua = null;
        this.eub = null;
    }

    @Override
    public void a(aqH aqH2) {
        int n;
        int n2;
        int n3;
        int n4;
        this.o = aqH2.bGI();
        this.ehO = aqH2.bGI();
        this.etV = aqH2.bxv();
        this.etW = aqH2.bGL().intern();
        int n5 = aqH2.bGI();
        this.etX = new aOG[n5];
        for (n4 = 0; n4 < n5; ++n4) {
            this.etX[n4] = new aOG();
            ((aOg)this.etX[n4]).a(aqH2);
        }
        n4 = aqH2.bGI();
        this.etY = new aOG[n4];
        for (n3 = 0; n3 < n4; ++n3) {
            this.etY[n3] = new aOG();
            ((aOg)this.etY[n3]).a(aqH2);
        }
        n3 = aqH2.bGI();
        this.etZ = new aOF[n3];
        for (n2 = 0; n2 < n3; ++n2) {
            this.etZ[n2] = new aOF();
            ((aOf)this.etZ[n2]).a(aqH2);
        }
        n2 = aqH2.bGI();
        this.eua = new aOH[n2];
        for (n = 0; n < n2; ++n) {
            this.eua[n] = new aOH();
            this.eua[n].a(aqH2);
        }
        n = aqH2.bGI();
        this.eub = new aOI[n];
        for (int i = 0; i < n; ++i) {
            this.eub[i] = new aOI();
            ((aOi)this.eub[i]).a(aqH2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.oBi.d();
    }
}
