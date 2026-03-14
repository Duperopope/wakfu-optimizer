/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fyi
implements aqz {
    protected int o;
    protected String asF;
    protected fvd tyG;

    public int d() {
        return this.o;
    }

    public String aGr() {
        return this.asF;
    }

    public fvd gnz() {
        return this.tyG;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.asF = null;
        this.tyG = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.asF = aqH2.bGL().intern();
        if (aqH2.aTf() != 0) {
            this.tyG = new fvd();
            this.tyG.a(aqH2);
        } else {
            this.tyG = null;
        }
    }

    @Override
    public final int bGA() {
        return ewj.ozG.d();
    }
}
