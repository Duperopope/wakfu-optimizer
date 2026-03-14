/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fxh
implements aqz {
    protected int o;
    protected float epy;
    protected String eik;
    protected int epz;

    public int d() {
        return this.o;
    }

    public float ctb() {
        return this.epy;
    }

    public String clB() {
        return this.eik;
    }

    public int ctc() {
        return this.epz;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.epy = 0.0f;
        this.eik = null;
        this.epz = 0;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.epy = aqH2.bGH();
        this.eik = aqH2.bGL().intern();
        this.epz = aqH2.bGI();
    }

    @Override
    public final int bGA() {
        return ewj.ozr.d();
    }
}
