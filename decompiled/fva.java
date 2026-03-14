/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewE
 *  ewj
 */
public class fva
implements aqz {
    protected int o;
    protected fvb[] tyU;
    protected byte tyV;

    public int d() {
        return this.o;
    }

    public fvb[] gnN() {
        return this.tyU;
    }

    public byte gnO() {
        return this.tyV;
    }

    public ewE gnP() {
        return ewE.ew((byte)this.tyV);
    }

    @Override
    public void reset() {
        this.o = 0;
        this.tyU = null;
        this.tyV = 0;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        int n = aqH2.bGI();
        this.tyU = new fvb[n];
        for (int i = 0; i < n; ++i) {
            this.tyU[i] = new fvb();
            this.tyU[i].a(aqH2);
        }
        this.tyV = aqH2.aTf();
    }

    @Override
    public final int bGA() {
        return ewj.ozR.d();
    }
}
