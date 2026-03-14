/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fuM
implements aqz {
    protected int o;
    protected int ehO;
    protected int ehP;
    protected fvd tyG;

    public int d() {
        return this.o;
    }

    public int clf() {
        return this.ehO;
    }

    public int clg() {
        return this.ehP;
    }

    public fvd gnz() {
        return this.tyG;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.ehO = 0;
        this.ehP = 0;
        this.tyG = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.ehO = aqH2.bGI();
        this.ehP = aqH2.bGI();
        if (aqH2.aTf() != 0) {
            this.tyG = new fvd();
            this.tyG.a(aqH2);
        } else {
            this.tyG = null;
        }
    }

    @Override
    public final int bGA() {
        return ewj.oyx.d();
    }
}
