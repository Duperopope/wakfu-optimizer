/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aKV
implements aqz {
    protected int o;
    protected aKW[] egy;

    public int d() {
        return this.o;
    }

    public aKW[] cjK() {
        return this.egy;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.egy = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        int n = aqH2.bGI();
        this.egy = new aKW[n];
        for (int i = 0; i < n; ++i) {
            this.egy[i] = new aKW();
            this.egy[i].a(aqH2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.oAz.d();
    }
}
