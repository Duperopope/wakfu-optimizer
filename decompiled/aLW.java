/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aLW
implements aqz {
    protected short ejr;
    protected double ejs;

    public short cmJ() {
        return this.ejr;
    }

    public double cmK() {
        return this.ejs;
    }

    @Override
    public void reset() {
        this.ejr = 0;
        this.ejs = 0.0;
    }

    @Override
    public void a(aqH aqH2) {
        this.ejr = aqH2.bGG();
        this.ejs = aqH2.bGJ();
    }

    @Override
    public final int bGA() {
        return ewj.ozV.d();
    }
}
