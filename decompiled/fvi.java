/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fvi
implements aqz {
    protected int eiT;
    protected int[] eiU;

    public int cmk() {
        return this.eiT;
    }

    public int[] cml() {
        return this.eiU;
    }

    @Override
    public void reset() {
        this.eiT = 0;
        this.eiU = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.eiT = aqH2.bGI();
        this.eiU = aqH2.bGM();
    }

    @Override
    public final int bGA() {
        return ewj.oyL.d();
    }
}
