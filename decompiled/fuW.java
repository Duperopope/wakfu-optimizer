/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fuW
implements aqz {
    protected int o;
    protected byte eis;
    protected int[] eit;

    public int d() {
        return this.o;
    }

    public byte clJ() {
        return this.eis;
    }

    public int[] clK() {
        return this.eit;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.eis = 0;
        this.eit = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.eis = aqH2.aTf();
        this.eit = aqH2.bGM();
    }

    @Override
    public final int bGA() {
        return ewj.oAq.d();
    }
}
