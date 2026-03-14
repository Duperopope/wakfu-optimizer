/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aOL
implements aqz {
    protected int elt;
    protected aOM[] eut;

    public int coK() {
        return this.elt;
    }

    public aOM[] cyd() {
        return this.eut;
    }

    @Override
    public void reset() {
        this.elt = 0;
        this.eut = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.elt = aqH2.bGI();
        int n = aqH2.bGI();
        this.eut = new aOM[n];
        for (int i = 0; i < n; ++i) {
            this.eut[i] = new aOM();
            ((aOm)this.eut[i]).a(aqH2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.ozJ.d();
    }
}
