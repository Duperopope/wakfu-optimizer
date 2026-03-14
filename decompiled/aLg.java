/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aLg
implements aqz {
    protected int o;
    protected int ehe;
    protected boolean ehf;

    public int d() {
        return this.o;
    }

    public int cku() {
        return this.ehe;
    }

    public boolean ckv() {
        return this.ehf;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.ehe = 0;
        this.ehf = false;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.ehe = aqH2.bGI();
        this.ehf = aqH2.bxv();
    }

    @Override
    public final int bGA() {
        return ewj.oyv.d();
    }
}
