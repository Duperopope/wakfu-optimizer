/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
import java.sql.Timestamp;

public class aKY
implements aqz {
    protected int o;
    protected Timestamp egA;
    protected int egB;

    public int d() {
        return this.o;
    }

    public Timestamp cjM() {
        return this.egA;
    }

    public int cjN() {
        return this.egB;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.egA = null;
        this.egB = 0;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.egA = new Timestamp(aqH2.bGK());
        this.egB = aqH2.bGI();
    }

    @Override
    public final int bGA() {
        return ewj.oAk.d();
    }
}
