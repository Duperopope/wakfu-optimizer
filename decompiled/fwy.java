/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
import java.sql.Timestamp;

public class fwy
implements aqz {
    protected int o;
    protected int emN;
    protected int emO;
    protected long emP;
    protected Timestamp emQ;
    protected boolean emR;

    public int d() {
        return this.o;
    }

    public int cql() {
        return this.emN;
    }

    public int cqm() {
        return this.emO;
    }

    public long cqn() {
        return this.emP;
    }

    public Timestamp cqo() {
        return this.emQ;
    }

    public boolean cqp() {
        return this.emR;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.emN = 0;
        this.emO = 0;
        this.emP = 0L;
        this.emQ = null;
        this.emR = false;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.emN = aqH2.bGI();
        this.emO = aqH2.bGI();
        this.emP = aqH2.bGK();
        this.emQ = new Timestamp(aqH2.bGK());
        this.emR = aqH2.bxv();
    }

    @Override
    public final int bGA() {
        return ewj.oAE.d();
    }
}
