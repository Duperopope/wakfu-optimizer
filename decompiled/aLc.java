/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aLc
implements aqz {
    protected int efP;
    protected int[] egN;
    protected int[] egO;

    public int cjd() {
        return this.efP;
    }

    public int[] cjY() {
        return this.egN;
    }

    public int[] cjZ() {
        return this.egO;
    }

    @Override
    public void reset() {
        this.efP = 0;
        this.egN = null;
        this.egO = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.efP = aqH2.bGI();
        this.egN = aqH2.bGM();
        this.egO = aqH2.bGM();
    }

    @Override
    public final int bGA() {
        return ewj.oAT.d();
    }
}
