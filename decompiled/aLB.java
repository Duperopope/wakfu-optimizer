/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aLB
implements aqz {
    protected int o;
    protected aLC[] eiA;

    public int d() {
        return this.o;
    }

    public aLC[] clR() {
        return this.eiA;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.eiA = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        int n = aqH2.bGI();
        this.eiA = new aLC[n];
        for (int i = 0; i < n; ++i) {
            this.eiA[i] = new aLC();
            ((aLc)this.eiA[i]).a(aqH2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.ozR.d();
    }
}
